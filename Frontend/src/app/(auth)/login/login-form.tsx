"use client";

import {zodResolver} from "@hookform/resolvers/zod";
import {SubmitHandler, useForm} from "react-hook-form";
import {z} from "zod";
import {useState} from "react";
import {Button} from "@/components/ui/button";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card";
import {Input} from "@/components/ui/input";
import {useRouter} from "next/navigation";
import Link from "next/link";

const formSchema = z.object({
    email: z.string().email({message: "Invalid email address"}).optional(),
    username: z.string().min(4, {message: "Username must be at least 4 characters"}).max(16, {message: "Username must be at most 16 characters"}).optional(),
    password: z.string().min(6, {message: "Password must be at least 6 characters"}),
});

type FormSchema = z.infer<typeof formSchema>;

export function LoginForm() {
    const router = useRouter();
    const [customError, setCustomError] = useState<string | null>(null);
    const form = useForm<FormSchema>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            email: '',
            username: '',
            password: '',
        },
    });

    const onSubmit: SubmitHandler<FormSchema> = async (data) => {
        if (typeof window === 'undefined') {
            return;
        }

        setCustomError(null);

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                const responseData = await response.json();
                localStorage.setItem('authToken', responseData.token);
                router.push('/');
            } else {
                const errorData = await response.json();
                setCustomError(errorData.error || 'Login failed');
            }
        } catch (error) {
            if (error instanceof Error) {
                setCustomError('An unexpected error occurred: ' + error.message);
            } else {
                setCustomError('An unexpected error occurred');
            }
        }
    };

    return (
        <Card className="mx-auto max-w-sm">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <CardHeader className="pb-0">
                        <CardTitle className="text-2xl">Login</CardTitle>
                        <CardDescription className="mb-4">
                            Enter your email or username and password to log in to your account.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                        <div className="grid gap-4">
                            <FormField
                                control={form.control}
                                name="email"
                                render={({field}) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input placeholder="john@example.com" type="email" {...field} />
                                        </FormControl>
                                        <FormMessage/>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="username"
                                render={({field}) => (
                                    <FormItem>
                                        <FormLabel>Username</FormLabel>
                                        <FormControl>
                                            <Input placeholder="john_doe" {...field} />
                                        </FormControl>
                                        <FormMessage/>
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="password"
                                render={({field}) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input placeholder="******" type="password" {...field} />
                                        </FormControl>
                                        <FormMessage/>
                                    </FormItem>
                                )}
                            />
                            <Button type="submit" className="w-full">
                                Sign in
                            </Button>
                            {customError && (
                                <p className="text-red-500">{customError}</p>
                            )}
                        </div>
                        <div className="mt-4 text-center text-sm">
                            Don&apos;t have an account?{" "}
                            <Link href="/register" className="underline">
                                Sign up
                            </Link>
                        </div>
                    </CardContent>
                </form>
            </Form>
        </Card>
    );
}
